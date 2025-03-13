import React from 'react';
import { Github, Mail } from 'lucide-react';

function TeamPage() {
    const team = [
        {
          name: "Brandon Tran",
          role: "Lead Developer",
          image: "https://media.discordapp.net/attachments/909605712311758919/1348117526642692228/image0.jpg?ex=67ce4bc9&is=67ccfa49&hm=96e5cacd267dd4b4a7182fdcf03837b0f164c761507ad9df1dec6de16ae72903&=&format=webp&width=693&height=960",
          email: "brandontran222@gmail.com",
          github: "BrandonTran03"
        },
        {
          name: "Leonardo Moodley",
          role: "Lead Developer",
          image: "https://media.discordapp.net/attachments/909605712311758919/1348117526894084218/image.png?ex=67ce4bc9&is=67ccfa49&hm=d968b8a0db96a4c79a24f4d0835515ac5d7366738e30ceaf728c9a31a217932b&=&format=webp&quality=lossless",
          email: "leo.moodley@outlook.com",
          github: "LeoMoodley"
        }
      ];

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 py-8 relative z-0">
            <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-16 px-4">
                <div className="max-w-4xl mx-auto">
                    <h1 className="text-4xl font-bold text-center text-gray-900 mb-2">Our Team</h1>
                    <p className="text-center text-gray-600 mb-12">Meet the minds behind our innovation</p>
                    
                    <div className="grid md:grid-cols-2 gap-12">
                    {team.map((member) => (
                        <div key={member.name} className="bg-white rounded-xl shadow-lg overflow-hidden transform transition duration-300 hover:scale-105">
                        <div className="aspect-w-4 aspect-h-3">
                            <img 
                            src={member.image} 
                            alt={member.name}
                            className="w-full h-64 object-cover"
                            />
                        </div>
                        <div className="p-6">
                            <h3 className="text-xl font-semibold text-gray-900">{member.name}</h3>
                            <p className="text-gray-600 mb-4">{member.role}</p>
                            
                            <div className="space-y-3">
                            <a 
                                href={`mailto:${member.email}`}
                                className="flex items-center text-gray-700 hover:text-blue-600 transition-colors"
                            >
                                <Mail className="w-5 h-5 mr-2" />
                                <span>{member.email}</span>
                            </a>
                            
                            <a 
                                href={`https://github.com/${member.github}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center text-gray-700 hover:text-blue-600 transition-colors"
                            >
                                <Github className="w-5 h-5 mr-2" />
                                <span>@{member.github}</span>
                            </a>
                            </div>
                        </div>
                        </div>
                    ))}
                    </div>
                </div>
                </div>
            </main>
        </div>
    );
}

export default TeamPage